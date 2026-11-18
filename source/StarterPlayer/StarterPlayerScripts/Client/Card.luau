-- StarterPlayerScripts/Client/Card.luau
-- Единая карточка зверя (сумка, коллекция, раскрытие, витрина): рамка цвета редкости, 3D-модель,
-- название, вес, цена, множитель броска, мутация, метки «НОВЫЙ»/«📦».
local RS = game:GetService("ReplicatedStorage")
local Fauna150 = require(game:GetService("ReplicatedStorage"):WaitForChild("Fauna150"))
local RunService = game:GetService("RunService")

local Config = require(RS.Shared.Config)
local Num = require(RS.Shared.Num)
local Util = require(RS.Shared.Util)
local UI = require(script.Parent.UIKit)
local Theme = require(script.Parent.Theme)

local Card = {}

export type Opts = {
	size: Vector2?,
	locked: boolean?,
	isNew: boolean?,
	spin: number?,
	onClick: (() -> ())?,
	showPrice: boolean?,
	count: number?,
	selected: boolean?,
	parent: Instance?,
	layoutOrder: number?,
	zIndex: number?,
}

local animated: { [Frame]: { grad: UIGradient, rainbow: boolean } } = {}
RunService.RenderStepped:Connect(function(dt)
	local t = os.clock()
	for f, a in animated do
		if not f.Parent then
			animated[f] = nil
		elseif f.Visible then
			a.grad.Rotation = (a.grad.Rotation + dt * 40) % 360
			if a.rainbow then
				a.grad.Color = ColorSequence.new(Theme.rainbow(t), Theme.rainbow(t + 1.5))
			end
		end
	end
end)

local function silhouette(vp: ViewportFrame)
	vp.Ambient = Color3.new(0, 0, 0)
	vp.LightColor = Color3.new(0, 0, 0)
	vp.ImageColor3 = Color3.fromRGB(30, 30, 40)
end

function Card.model(spId: string, mut: string?): Model?
	-- Все 150 видов собираются из данных коллекции (Fauna150); старые шаблоны Animals — запасной путь
	local tpl: Model? = Fauna150.Template(spId)
	if not tpl then
		local old = RS:FindFirstChild("Animals") and RS.Animals:FindFirstChild(spId)
		if not old or not old:IsA("Model") then
			return nil
		end
		tpl = old
	end
	if mut then
		local m = (tpl :: Model):Clone()
		Util.applyMutation(m, mut)
		return m
	end
	return tpl
end

function Card.new(spId: string, item: any?, o: Opts?): Frame
	local opts: Opts = o or {}
	local sp = Config.SPECIES_BY_ID[spId]
	local rar = Theme.rarity(sp and sp.rarity or 1)
	local size = opts.size or Vector2.new(160, 212)
	local k = size.X / 160
	local z = opts.zIndex or 3
	local f = Instance.new("Frame")
	f.Name = "Card_" .. spId
	f.Size = UDim2.fromOffset(size.X, size.Y)
	f.BackgroundColor3 = Color3.new(1, 1, 1)
	f.BorderSizePixel = 0
	f.ZIndex = z
	if opts.layoutOrder then
		f.LayoutOrder = opts.layoutOrder
	end
	UI.corner(math.floor(16 * k)).Parent = f
	local locked = opts.locked == true
	local c1 = locked and Color3.fromRGB(70, 74, 92) or rar.color
	local c2 = locked and Color3.fromRGB(34, 36, 50) or rar.dark
	local g = UI.gradient(c1, c2, 90)
	g.Parent = f
	local st = UI.stroke(opts.selected and Color3.new(1, 1, 1) or Color3.fromRGB(12, 12, 22), opts.selected and 5 or 3, 0, true)
	st.Parent = f
	if not locked and sp and sp.rarity >= 5 then
		g.Color = ColorSequence.new(rar.color, rar.dark)
		animated[f] = { grad = g, rainbow = sp.rarity >= 6 }
	end
	-- узор-полосы
	local stripes = Instance.new("Frame")
	stripes.BackgroundColor3 = Color3.new(1, 1, 1)
	stripes.BackgroundTransparency = 0.88
	stripes.BorderSizePixel = 0
	stripes.Size = UDim2.new(1, 0, 0.5, 0)
	stripes.ZIndex = z
	UI.corner(math.floor(16 * k)).Parent = stripes
	stripes.Parent = f
	-- 3D-модель
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.Size = UDim2.new(1, -10 * k, 0.6, 0)
	holder.Position = UDim2.new(0, 5 * k, 0, 22 * k)
	holder.ZIndex = z + 1
	holder.Parent = f
	if not locked and sp and sp.rarity >= 3 then
		UI.glow(holder, rar.color, size.X * 1.1, 0.35).ZIndex = z + 1
	end
	local model = Card.model(spId, item and item.mut or nil)
	if model then
		local vp = UI.viewport(model, { ZIndex = z + 2 }, math.rad(-30), opts.spin)
		if locked then
			silhouette(vp)
		end
		vp.Parent = holder
	else
		UI.label({ Text = sp and sp.icon or "?", TextSize = 60 * k, Size = UDim2.fromScale(1, 1), ZIndex = z + 2, Parent = holder })
	end
	-- редкость
	local pill = UI.panel({ Color = locked and Theme.C.gray or rar.dark, Size = UDim2.fromOffset(10, 22 * k), Position = UDim2.fromOffset(6 * k, 6 * k), Radius = 8, LineThick = 2, ZIndex = z + 3, Parent = f })
	pill.AutomaticSize = Enum.AutomaticSize.X
	UI.pad(math.floor(6 * k), 0).Parent = pill
	UI.label({ Text = locked and "???" or string.upper(rar.name), TextSize = math.floor(13 * k), Size = UDim2.new(0, 10, 1, 0), AutoX = true, ZIndex = z + 4, Stroke = 2, Parent = pill })
	-- множитель броска
	if item and item.m and item.m > 1.01 then
		local ti = Theme.tier(Config.tierIndex(item.m))
		local mb = UI.label({ Text = Num.mult(item.m), TextSize = math.floor(20 * k), Color = ti.color, Size = UDim2.fromOffset(60 * k, 24 * k), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -6 * k, 0, 5 * k), XAlign = Enum.TextXAlignment.Right, ZIndex = z + 4, Parent = f })
		mb.Rotation = 8
	end
	-- имя
	UI.label({ Text = locked and "???" or (sp and sp.name or spId), TextSize = math.floor(19 * k), Size = UDim2.new(1, -8 * k, 0, 24 * k), Position = UDim2.new(0, 4 * k, 0.66, 0), ZIndex = z + 4, Scaled = true, MaxSize = math.floor(20 * k), Parent = f })
	-- вес и цена
	if item and not locked then
		local mult = item.wrapped and Config.WRAP_MULT or 1
		UI.label({ Text = "⚖️ " .. Num.weight(item.w), TextSize = math.floor(15 * k), Color = Theme.C.dim, Size = UDim2.new(1, -8 * k, 0, 20 * k), Position = UDim2.new(0, 4 * k, 0.66, 25 * k), ZIndex = z + 4, Stroke = 2, Parent = f })
		UI.label({ Text = "💰 " .. Num.short(item.price * mult), TextSize = math.floor(18 * k), Color = Theme.C.gold, Size = UDim2.new(1, -8 * k, 0, 22 * k), Position = UDim2.new(0, 4 * k, 0.66, 44 * k), ZIndex = z + 4, Parent = f })
	elseif opts.count and not locked then
		UI.label({ Text = "Caught: " .. tostring(opts.count), TextSize = math.floor(15 * k), Color = Theme.C.dim, Size = UDim2.new(1, -8 * k, 0, 20 * k), Position = UDim2.new(0, 4 * k, 0.66, 27 * k), ZIndex = z + 4, Stroke = 2, Parent = f })
	elseif locked and sp then
		UI.label({ Text = Config.ZONES[sp.zone].icon .. " " .. Config.ZONES[sp.zone].name, TextSize = math.floor(14 * k), Color = Theme.C.dim, Size = UDim2.new(1, -8 * k, 0, 20 * k), Position = UDim2.new(0, 4 * k, 0.66, 27 * k), ZIndex = z + 4, Stroke = 2, Parent = f })
	end
	-- мутация
	if item and item.mut and not locked then
		local mt = Config.MUTATIONS[item.mut]
		local mb = UI.panel({ Color = mt.color, Size = UDim2.fromOffset(10, 22 * k), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 0.6, 0), Radius = 10, LineThick = 2, ZIndex = z + 5, Parent = f })
		mb.AutomaticSize = Enum.AutomaticSize.X
		UI.pad(math.floor(6 * k), 0).Parent = mb
		UI.label({ Text = (item.mut == "gold" and "✨ " or "🌈 ") .. string.upper(mt.name) .. " ×" .. mt.mult, TextSize = math.floor(13 * k), Size = UDim2.new(0, 10, 1, 0), AutoX = true, ZIndex = z + 6, Stroke = 2, Parent = mb })
		if item.mut == "rainbow" then
			animated[mb] = { grad = mb:FindFirstChildOfClass("UIGradient") :: UIGradient, rainbow = true }
		end
	end
	if item and item.wrapped then
		UI.label({ Text = "📦", TextSize = math.floor(24 * k), Size = UDim2.fromOffset(30 * k, 30 * k), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -4 * k, 0.62, 0), ZIndex = z + 5, Stroke = 2, Parent = f })
	end
	if opts.isNew then
		local nb = UI.label({ Text = "NEW!", TextSize = math.floor(16 * k), Color = Theme.C.gold, Size = UDim2.fromOffset(70 * k, 22 * k), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(1, -16 * k, 0, 30 * k), Rotation = 14, ZIndex = z + 6, Parent = f })
		local _ = nb
	end
	if opts.onClick then
		local b = Instance.new("TextButton")
		b.BackgroundTransparency = 1
		b.Text = ""
		b.Size = UDim2.fromScale(1, 1)
		b.ZIndex = z + 8
		b.Parent = f
		local sc = Instance.new("UIScale")
		sc.Parent = f
		b.MouseEnter:Connect(function()
			UI.tween(sc, 0.12, { Scale = 1.05 }, Enum.EasingStyle.Back)
		end)
		b.MouseLeave:Connect(function()
			UI.tween(sc, 0.12, { Scale = 1 })
		end)
		b.Activated:Connect(function()
			sc.Scale = 0.92
			UI.tween(sc, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
			local cb = opts.onClick
			if cb then
				task.spawn(cb)
			end
		end)
	end
	if opts.parent then
		f.Parent = opts.parent
	end
	return f
end

return Card
