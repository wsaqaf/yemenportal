# == Schema Information
#
# Table name: topics
#
#  id           :integer          not null, primary key
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  topic_size   :integer
#  main_post_id :integer
#
# Indexes
#
#  index_topics_on_main_post_id  (main_post_id)
#

FactoryGirl.define do
  factory :topic do
    association :main_post, factory: :post
  end
end
