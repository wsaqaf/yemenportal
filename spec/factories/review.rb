FactoryGirl.define do
  factory :review do
    moderator factory: :user_moderator
    topic
    flag
  end
end
