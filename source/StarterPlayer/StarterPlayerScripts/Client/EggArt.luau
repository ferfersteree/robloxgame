-- StarterPlayerScripts/Client/EggArt.luau
-- Pre-rendered crystal egg pictures (tools/render_eggs.py) drawn at runtime with EditableImage.
-- Nothing is uploaded to Roblox: the pixels live in the child ModuleScripts (deflate + base64) and are
-- unpacked here once per egg, a few thousand steps per frame, so the shop never hitches.
-- If EditableImage is not available (setting, device), apply() returns false and the caller keeps its fallback.
local AssetService = game:GetService("AssetService")

local EggArt = {}
local cache: { [string]: any } = {}
local waiting: { [string]: { () -> () } } = {}
local failed: { [string]: boolean } = {}
local busy = false
local available: boolean? = nil -- can this client create an EditableImage at all? asked once, before any decoding

local function checkAvailable(): boolean
	if available == nil then
		available = pcall(function()
			local probe = AssetService:CreateEditableImage({ Size = Vector2.new(1, 1) })
			probe:Destroy()
		end)
	end
	return available :: boolean
end

local B64: { [number]: number } = {}
do
	local chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
	for i = 1, 64 do
		B64[string.byte(chars, i)] = i - 1
	end
end

local function b64decode(s: string): (buffer, number)
	local n = #s
	local pad = 0
	if string.byte(s, n) == 61 then
		pad += 1
	end
	if string.byte(s, n - 1) == 61 then
		pad += 1
	end
	local outLen = n // 4 * 3 - pad
	local out = buffer.create(outLen + 3)
	local o = 0
	for i = 1, n, 4 do
		if i > 1 and (i - 1) % 40000 == 0 then
			task.wait() -- every 10000 groups
		end
		local a, b, c, d = string.byte(s, i, i + 3)
		local v = bit32.lshift(B64[a], 18) + bit32.lshift(B64[b], 12) + bit32.lshift(B64[c] or 0, 6) + (B64[d] or 0)
		buffer.writeu8(out, o, bit32.rshift(v, 16))
		buffer.writeu8(out, o + 1, bit32.band(bit32.rshift(v, 8), 255))
		buffer.writeu8(out, o + 2, bit32.band(v, 255))
		o += 3
	end
	return out, outLen
end

local LENS = { 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258 }
local LEXT = { 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0 }
local DISTS = { 1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577 }
local DEXT = { 0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13 }
local ORDER = { 16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15 }

-- canonical Huffman table (same idea as zlib's puff.c): lengths[off .. off+n-1] are code lengths (1-based table)
local function construct(lengths: { number }, n: number, off: number): any
	local count = table.create(15, 0)
	for s = 0, n - 1 do
		local l = lengths[off + s]
		if l > 0 then
			count[l] += 1
		end
	end
	local offs = table.create(16, 0)
	for len = 1, 14 do
		offs[len + 1] = offs[len] + count[len]
	end
	local symbol = {}
	for s = 0, n - 1 do
		local l = lengths[off + s]
		if l > 0 then
			symbol[offs[l] + 1] = s
			offs[l] += 1
		end
	end
	return { count = count, symbol = symbol }
end

local FIXED_LEN: any, FIXED_DIST: any
do
	local l = {}
	for i = 1, 144 do
		l[i] = 8
	end
	for i = 145, 256 do
		l[i] = 9
	end
	for i = 257, 280 do
		l[i] = 7
	end
	for i = 281, 288 do
		l[i] = 8
	end
	FIXED_LEN = construct(l, 288, 1)
	local d = {}
	for i = 1, 30 do
		d[i] = 5
	end
	FIXED_DIST = construct(d, 30, 1)
end

-- raw deflate stream -> bytes. Yields (task.wait) every 5000 symbols so a frame never gets more than a few ms of work.
local function inflate(src: buffer, outLen: number): buffer
	local out = buffer.create(outLen)
	local op, pos, bitbuf, bitcnt, steps = 0, 0, 0, 0, 0
	local function bits(need: number): number
		local val = bitbuf
		while bitcnt < need do
			val = bit32.bor(val, bit32.lshift(buffer.readu8(src, pos), bitcnt))
			pos += 1
			bitcnt += 8
		end
		bitbuf = bit32.rshift(val, need)
		bitcnt -= need
		return bit32.band(val, bit32.lshift(1, need) - 1)
	end
	local function decode(h: any): number
		local code, first, index = 0, 0, 0
		for len = 1, 15 do
			code = bit32.bor(code, bits(1))
			local cnt = h.count[len]
			if code - cnt < first then
				return h.symbol[index + (code - first) + 1]
			end
			index += cnt
			first += cnt
			first = bit32.lshift(first, 1)
			code = bit32.lshift(code, 1)
		end
		error("bad huffman code")
	end
	local function codes(lencode: any, distcode: any)
		while true do
			local sym = decode(lencode)
			if sym < 256 then
				buffer.writeu8(out, op, sym)
				op += 1
			elseif sym == 256 then
				return
			else
				sym -= 257
				local len = LENS[sym + 1] + bits(LEXT[sym + 1])
				local ds = decode(distcode)
				local dist = DISTS[ds + 1] + bits(DEXT[ds + 1])
				for i = 0, len - 1 do
					buffer.writeu8(out, op + i, buffer.readu8(out, op + i - dist))
				end
				op += len
			end
			steps += 1
			if steps % 5000 == 0 then
				task.wait()
			end
		end
	end
	repeat
		local last = bits(1)
		local kind = bits(2)
		if kind == 0 then
			bitbuf, bitcnt = 0, 0
			local len = buffer.readu8(src, pos) + buffer.readu8(src, pos + 1) * 256
			pos += 4
			for i = 0, len - 1 do
				buffer.writeu8(out, op + i, buffer.readu8(src, pos + i))
			end
			pos += len
			op += len
		elseif kind == 1 then
			codes(FIXED_LEN, FIXED_DIST)
		elseif kind == 2 then
			local nlen = bits(5) + 257
			local ndist = bits(5) + 1
			local ncode = bits(4) + 4
			local lengths = {}
			for i = 1, 19 do
				lengths[i] = 0
			end
			for i = 1, ncode do
				lengths[ORDER[i] + 1] = bits(3)
			end
			local lc = construct(lengths, 19, 1)
			local ll = {}
			local idx = 0
			while idx < nlen + ndist do
				local sym = decode(lc)
				if sym < 16 then
					ll[idx + 1] = sym
					idx += 1
				else
					local prev, rep = 0, 0
					if sym == 16 then
						prev = ll[idx]
						rep = 3 + bits(2)
					elseif sym == 17 then
						rep = 3 + bits(3)
					else
						rep = 11 + bits(7)
					end
					for _ = 1, rep do
						ll[idx + 1] = prev
						idx += 1
					end
				end
			end
			codes(construct(ll, nlen, 1), construct(ll, ndist, nlen + 1))
		else
			error("bad deflate block")
		end
	until last == 1
	return out
end

local function adler32(buf: buffer, len: number): number
	local a, b = 1, 0
	for i = 0, len - 1 do
		a = (a + buffer.readu8(buf, i)) % 65521
		b = (b + a) % 65521
		if i % 30000 == 29999 then
			task.wait()
		end
	end
	return b * 65536 + a
end

local function build(key: string): any?
	local mod = script:FindFirstChild(key)
	if not mod then
		return nil
	end
	local data = require(mod) :: any
	local src = b64decode(data.z)
	local raw = inflate(src, data.w * data.h * 4)
	if adler32(raw, data.w * data.h * 4) ~= data.adler then
		warn("[EggArt] checksum mismatch for " .. key)
		return nil
	end
	local img = AssetService:CreateEditableImage({ Size = Vector2.new(data.w, data.h) })
	img:WritePixelsBuffer(Vector2.zero, Vector2.new(data.w, data.h), raw)
	return img
end

-- Decode once and share; many labels can show the same egg. Calls back on the main thread when ready.
local function whenReady(key: string, cb: (any?) -> ())
	if cache[key] then
		cb(cache[key])
		return
	end
	if failed[key] then
		cb(nil)
		return
	end
	if waiting[key] then
		table.insert(waiting[key], cb)
		return
	end
	waiting[key] = { cb }
	task.spawn(function()
		if not checkAvailable() then
			-- EditableImage is off (experience setting, device): fail every picture at once, no wasted decoding
			failed[key] = true
			local list0 = waiting[key]
			waiting[key] = nil
			for _, f in list0 do
				f(nil)
			end
			return
		end
		-- one picture at a time, in the order they were asked for (the visible ones first)
		while busy do
			task.wait()
		end
		busy = true
		local ok, img = pcall(build, key)
		busy = false
		if ok and img then
			cache[key] = img
		else
			failed[key] = true
			if not ok then
				warn("[EggArt] " .. key .. " failed: " .. tostring(img))
			end
		end
		local list = waiting[key]
		waiting[key] = nil
		for _, f in list do
			f(cache[key])
		end
	end)
end

-- Draw egg `key` into an ImageLabel. onFail runs if the picture could not be made (the caller keeps its fallback).
function EggArt.apply(label: ImageLabel, key: string, onFail: (() -> ())?)
	whenReady(key, function(img)
		if img and label.Parent then
			label.ImageContent = Content.fromObject(img)
		elseif not img and onFail and label.Parent then
			onFail()
		end
	end)
end

-- Decode pictures ahead of time (the hatch window needs its egg at once, not after the whole queue)
function EggArt.preload(keys: { string })
	for _, k in keys do
		whenReady(k, function() end)
	end
end

function EggArt.has(key: string): boolean
	return script:FindFirstChild(key) ~= nil and not failed[key]
end

return EggArt
