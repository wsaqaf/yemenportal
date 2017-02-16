FactoryGirl.define do
  factory :post do
    sequence(:description) { |n| "Description_#{n}" }
    sequence(:title) { |n| "Title_#{n}" }
    sequence(:link) { |n| "Link_#{n}" }
    pub_date Time.new
  end
end
