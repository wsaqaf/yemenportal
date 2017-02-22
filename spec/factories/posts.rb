FactoryGirl.define do
  factory :post do
    sequence(:description) { |n| "Description_#{n}" }
    sequence(:title) { |n| "Title_#{n}" }
    sequence(:link) { |n| "Link_#{n}" }
    published_at Time.new
  end
end
