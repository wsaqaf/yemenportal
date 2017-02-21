FactoryGirl.define do
  factory :source do
    sequence(:link) { |n| "www.source_#{n}@gar.com" }
  end
end
