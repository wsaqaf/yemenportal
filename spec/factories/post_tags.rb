# == Schema Information
#
# Table name: post_tags
#
#  id         :integer          not null, primary key
#  name       :string
#  user_id    :integer
#  post_id    :integer
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_post_tags_on_post_id  (post_id)
#  index_post_tags_on_user_id  (user_id)
#

FactoryGirl.define do
  factory :post_tag do
    sequence(:name) { |n| "name_#{n}" }
    association :user
    association :post
  end
end
