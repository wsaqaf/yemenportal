FactoryGirl.define do
  factory :post_category do
    association :post
    association :category
  end
end
