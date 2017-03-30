FactoryGirl.define do
  factory :source do
    sequence(:link) { |n| "www.source_#{n}@gar.com" }
    association :category
    whitelisted false
  end
end
