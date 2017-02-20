FactoryGirl.define do
  factory :category do
    sequence(:name) { |n| "Category_#{n}" }
  end
end
