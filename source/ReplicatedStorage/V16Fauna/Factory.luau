--!strict
-- Переходник: вся фауна игры (150 видов) теперь живёт в ReplicatedStorage.Fauna150.
-- Старые ModelsData/MotionData остаются в игре только как архив и не читаются.
local Fauna = require(game:GetService("ReplicatedStorage"):WaitForChild("Fauna150")) :: any
local Factory = {}

function Factory.Get(id: string): any?
	return Fauna.Get(id)
end

function Factory.Create(id: string): Model?
	return Fauna.Create(id)
end

return Factory
