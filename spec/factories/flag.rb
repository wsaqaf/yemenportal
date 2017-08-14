FactoryGirl.define do
  factory :flag do
    name Faker::Lorem.word
    color Faker::Color.hex_color

    factory(:resolve_flag) do
      resolve true
    end
  end
end
