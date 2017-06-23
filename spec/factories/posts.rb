# == Schema Information
#
# Table name: posts
#
#  id           :integer          not null, primary key
#  description  :text
#  published_at :datetime         not null
#  link         :string           not null
#  title        :string           not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  state        :string           default("pending"), not null
#  photo_url    :string
#  topic_id     :integer
#  stemmed_text :text             default("")
#  source_id    :integer          not null
#
# Indexes
#
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#  index_posts_on_topic_id      (topic_id)
#

FactoryGirl.define do
  factory :post do
    sequence(:description) { |n| "Description_#{n}" }
    sequence(:title) { |n| "Title_#{n}" }
    sequence(:link) { |n| "Link_#{n}" }
    sequence(:stemmed_text) { |n| "stemmed_text_#{n}" }
    state "pending"
    association :source
    association :topic
    published_at Time.new
  end
end
