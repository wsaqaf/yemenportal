# == Schema Information
#
# Table name: comments
#
#  id         :integer          not null, primary key
#  user_id    :integer
#  body       :text             not null
#  post_id    :integer
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_comments_on_post_id  (post_id)
#  index_comments_on_user_id  (user_id)
#

FactoryGirl.define do
  factory :comment do
    sequence(:body) { |n| "Comment number #{n}." }
    association :user
    association :post
  end
end
