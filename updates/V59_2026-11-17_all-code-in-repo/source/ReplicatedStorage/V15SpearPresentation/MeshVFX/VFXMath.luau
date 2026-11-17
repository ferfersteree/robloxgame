--!strict
--[[
	VFXMath
	Pure geometry helpers (no services) - unit-tested under Lune with real CFrame math.

	Conventions used by every effect in this library:
	  * An effect "frame" is a CFrame whose UpVector is the surface normal / slash plane
	    normal and whose LookVector is the forward direction of the effect.
	  * Arc angles are measured around the frame's +Y axis starting from -Z (forward),
	    positive = counter-clockwise seen from above (towards -X / the left).
]]

local VFXMath = {}

local EPSILON = 1e-4

--[[
	Builds a right-handed CFrame at `position` whose UpVector is `normal` and whose
	LookVector is `forwardHint` projected onto the surface plane.

	This replaces the classic (and wrong) `CFrame.fromMatrix(pos, right, up, -look)`
	pattern, which produces a mirrored (left-handed) matrix when `look = right:Cross(up)`.
]]
function VFXMath.alignToNormal(position: Vector3, normal: Vector3, forwardHint: Vector3?): CFrame
	local up = if normal.Magnitude > EPSILON then normal.Unit else Vector3.yAxis
	local forward = forwardHint or -Vector3.zAxis
	forward -= up * forward:Dot(up)
	if forward.Magnitude < EPSILON then
		-- Hint parallel to the normal: pick any stable perpendicular.
		forward = Vector3.xAxis - up * up.X
		if forward.Magnitude < EPSILON then
			forward = Vector3.zAxis - up * up.Z
		end
	end
	forward = forward.Unit
	local right = forward:Cross(up)
	-- fromMatrix(pos, X, Y, Z): X = right, Y = up, Z = back (= -look). X:Cross(Y) == Z.
	return CFrame.fromMatrix(position, right, up, -forward)
end

--[[
	CFrame at `position` whose LookVector is exactly `direction` (UpVector as close to
	`upHint` as possible). Same result as CFrame.lookAt(position, position + direction),
	built with fromMatrix so it also runs in test runtimes whose lookAt is unreliable.
]]
function VFXMath.lookAlong(position: Vector3, direction: Vector3, upHint: Vector3?): CFrame
	local look = if direction.Magnitude > EPSILON then direction.Unit else -Vector3.zAxis
	local up = upHint or Vector3.yAxis
	local right = look:Cross(up)
	if right.Magnitude < EPSILON then
		right = look:Cross(if math.abs(look.X) < 0.9 then Vector3.xAxis else Vector3.zAxis)
	end
	right = right.Unit
	return CFrame.fromMatrix(position, right, right:Cross(look), -look)
end

-- Point on a circle of radius r lying in the frame's XZ plane, at arc angle `angle`.
function VFXMath.arcPoint(radius: number, angle: number): Vector3
	return Vector3.new(-radius * math.sin(angle), 0, -radius * math.cos(angle))
end

-- Unit tangent of the arc at `angle`, pointing towards increasing angles.
function VFXMath.arcTangent(angle: number): Vector3
	return Vector3.new(-math.cos(angle), 0, math.sin(angle))
end

--[[
	Local CFrame for an Attachment sitting on the arc so that a Beam's Bezier handles
	(which extend along the attachment's +X axis) follow the circle.
]]
function VFXMath.arcAttachmentCFrame(radius: number, angle: number): CFrame
	return CFrame.fromMatrix(VFXMath.arcPoint(radius, angle), VFXMath.arcTangent(angle), Vector3.yAxis)
end

--[[
	Beam CurveSize that makes a cubic Bezier approximate a circular arc of `sweep`
	radians (k = 4/3 * tan(sweep / 4) * r). Error < 0.03% of the radius for 90 deg arcs,
	so split larger arcs into <= 90 deg pieces.
]]
function VFXMath.arcCurveSize(radius: number, sweep: number): number
	return (4 / 3) * math.tan(sweep / 4) * radius
end

-- Evaluates a cubic Bezier (used by tests and by effects that need points along a beam).
function VFXMath.bezier(p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3, t: number): Vector3
	local u = 1 - t
	return p0 * (u * u * u) + p1 * (3 * u * u * t) + p2 * (3 * u * t * t) + p3 * (t * t * t)
end

-- Random unit vector inside a cone of half-angle `angle` (radians) around `direction`.
function VFXMath.randomInCone(rng: Random, direction: Vector3, angle: number): Vector3
	local dir = if direction.Magnitude > EPSILON then direction.Unit else Vector3.yAxis
	-- Uniform on the spherical cap.
	local cosAngle = math.cos(angle)
	local z = cosAngle + (1 - cosAngle) * rng:NextNumber()
	local phi = rng:NextNumber() * 2 * math.pi
	local r = math.sqrt(math.max(0, 1 - z * z))
	local localDir = Vector3.new(r * math.cos(phi), r * math.sin(phi), -z)
	-- Frame whose LookVector (-Z) is `dir`.
	return VFXMath.lookAlong(Vector3.zero, dir):VectorToWorldSpace(localDir)
end

function VFXMath.randomRange(rng: Random, min: number, max: number): number
	return min + (max - min) * rng:NextNumber()
end

-- Opacity (1 = visible) <-> Transparency (1 = invisible) helpers for layered fades.
function VFXMath.combineTransparency(baseTransparency: number, opacity: number): number
	return 1 - (1 - baseTransparency) * math.clamp(opacity, 0, 1)
end

--[[
	Deterministic ring layout used by crater/debris effects. Returns `count` angles
	spread around the circle with a random jitter of +-(jitter * step / 2).
	Seeded -> every client builds the exact same crater.
]]
function VFXMath.ringAngles(rng: Random, count: number, jitter: number): { number }
	local angles = table.create(count)
	local step = 2 * math.pi / count
	local offset = rng:NextNumber() * step
	for i = 1, count do
		angles[i] = offset + (i - 1) * step + (rng:NextNumber() - 0.5) * step * jitter
	end
	return angles
end

return VFXMath
