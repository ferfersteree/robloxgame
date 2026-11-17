--!strict
--[[
	BeamArc
	A circular arc (or full ring) drawn with Beams whose Bezier handles follow the circle.
	Used as the zero-asset fallback for slashes and shockwaves, and useful on its own for
	wind rings, sword trails and aura loops.

	The arc lives in the holder's local XZ plane (Y = up); angles start at -Z (forward)
	and grow counter-clockwise (towards -X). Each Beam covers <= 90 deg so the Bezier
	stays within 0.03% of a true circle.

	Usage:
		local arc = BeamArc.new(folder, 2) -- 2 pieces
		arc:setFrame(cframe)
		arc:set(radius, -math.rad(80), math.rad(80), function(u) return math.sin(math.pi * u) end, 0.2)
]]

local VFXMath = require(script.Parent.VFXMath)

export type WidthFn = (u: number) -> number

export type BeamArc = {
	holder: BasePart,
	beams: { Beam },
	attachments: { Attachment },
	setFrame: (self: BeamArc, cframe: CFrame) -> (),
	set: (
		self: BeamArc,
		radius: number,
		startAngle: number,
		endAngle: number,
		width: WidthFn,
		transparency: number
	) -> (),
	setColor: (self: BeamArc, color: Color3) -> (),
	setEnabled: (self: BeamArc, enabled: boolean) -> (),
}

export type Options = {
	color: Color3?,
	lightEmission: number?,
	lightInfluence: number?,
	faceCamera: boolean?,
	texture: string?,
	textureLength: number?,
	zOffset: number?,
	segmentsPerPiece: number?,
}

local BeamArc = {}
BeamArc.__index = BeamArc

function BeamArc.new(parent: Instance, pieces: number, options: Options?): BeamArc
	local opts: Options = options or {}
	local holder = Instance.new("Part")
	holder.Name = "BeamArc"
	holder.Anchored = true
	holder.CanCollide = false
	holder.CanTouch = false
	holder.CanQuery = false
	holder.CastShadow = false
	holder.Transparency = 1
	holder.Size = Vector3.new(0.1, 0.1, 0.1)
	holder.CFrame = CFrame.new(0, -5e4, 0)

	local attachments: { Attachment } = {}
	for i = 1, pieces + 1 do
		local a = Instance.new("Attachment")
		a.Name = `A{i}`
		a.Parent = holder
		attachments[i] = a
	end

	local beams: { Beam } = {}
	for i = 1, pieces do
		local beam = Instance.new("Beam")
		beam.Attachment0 = attachments[i]
		beam.Attachment1 = attachments[i + 1]
		beam.FaceCamera = if opts.faceCamera == nil then true else opts.faceCamera
		beam.LightEmission = opts.lightEmission or 1
		beam.LightInfluence = opts.lightInfluence or 0
		beam.Segments = opts.segmentsPerPiece or 12
		beam.Color = ColorSequence.new(opts.color or Color3.new(1, 1, 1))
		beam.ZOffset = opts.zOffset or 0
		if opts.texture then
			beam.Texture = opts.texture
			beam.TextureMode = Enum.TextureMode.Stretch
			beam.TextureLength = opts.textureLength or 1
		end
		beam.Enabled = false
		beam.Parent = holder
		beams[i] = beam
	end

	holder.Parent = parent

	local self = setmetatable({
		holder = holder,
		beams = beams,
		attachments = attachments,
	}, BeamArc)
	return (self :: any) :: BeamArc
end

function BeamArc.setFrame(self: BeamArc, cframe: CFrame)
	self.holder.CFrame = cframe
end

-- `width(u)` receives u in [0, 1] along the arc (0 = start, 1 = end).
function BeamArc.set(
	self: BeamArc,
	radius: number,
	startAngle: number,
	endAngle: number,
	width: WidthFn,
	transparency: number
)
	local pieces = #self.beams
	local sweep = (endAngle - startAngle) / pieces
	local curve = VFXMath.arcCurveSize(radius, math.abs(sweep))
	-- Beams handles follow +X of attachment0 and -X of attachment1: when the arc runs
	-- clockwise (negative sweep) the tangents flip, which arcAttachmentCFrame handles
	-- through the sign of `direction`.
	local direction = if sweep >= 0 then 1 else -1
	local seq = NumberSequence.new(math.clamp(transparency, 0, 1))

	for i, attachment in self.attachments do
		local angle = startAngle + sweep * (i - 1)
		local cf = VFXMath.arcAttachmentCFrame(radius, angle)
		if direction < 0 then
			cf *= CFrame.Angles(0, math.pi, 0) -- flip X (tangent) and Z, keep Y up
		end
		attachment.CFrame = cf
	end
	for i, beam in self.beams do
		beam.CurveSize0 = curve
		beam.CurveSize1 = curve
		beam.Width0 = math.max(width((i - 1) / pieces), 0)
		beam.Width1 = math.max(width(i / pieces), 0)
		beam.Transparency = seq
	end
end

function BeamArc.setColor(self: BeamArc, color: Color3)
	local seq = ColorSequence.new(color)
	for _, beam in self.beams do
		beam.Color = seq
	end
end

function BeamArc.setEnabled(self: BeamArc, enabled: boolean)
	for _, beam in self.beams do
		beam.Enabled = enabled
	end
	if not enabled then
		self.holder.CFrame = CFrame.new(0, -5e4, 0)
	end
end

return BeamArc
