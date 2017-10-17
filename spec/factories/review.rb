FactoryGirl.define do
  factory :review do
    moderator factory: :user_moderator
    post
    flag
  end
end
