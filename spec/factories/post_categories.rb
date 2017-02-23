# == Schema Information
#
# Table name: post_categories
#
#  id          :integer          not null, primary key
#  post_id     :integer          not null
#  category_id :integer          not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_post_categories_on_category_id  (category_id)
#  index_post_categories_on_post_id      (post_id)
#

FactoryGirl.define do
  factory :post_category do
    association :post
    association :category
  end
end
