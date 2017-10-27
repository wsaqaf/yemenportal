FactoryGirl.define do
  factory :flag do
    name Faker::Lorem.word
    color Faker::Color.hex_color
    rate Faker::Number.between(-1, 1)

    factory(:resolve_flag) do
      resolve true
    end
  end
end
