# == Schema Information
#
# Table name: post_tags
#
#  id          :integer          not null, primary key
#  user_id     :integer
#  post_id     :integer
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  name        :string
#  description :string
#
# Indexes
#
#  index_post_tags_on_post_id  (post_id)
#  index_post_tags_on_user_id  (user_id)
#

FactoryGirl.define do
  Tag.create(name: "tag_name")

  factory :post_tag do
    association :user
    association :post
    sequence(:name) { |n| "Name_#{n}" }
  end
end
