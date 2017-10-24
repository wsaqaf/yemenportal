# == Schema Information
#
# Table name: post_views
#
#  id         :integer          not null, primary key
#  post_id    :integer          not null
#  user_id    :integer
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_post_views_on_post_id  (post_id)
#  index_post_views_on_user_id  (user_id)
#

FactoryGirl.define do
  factory :post_view do
    association :post

    trait :with_user do
      association :user
    end
  end
end
