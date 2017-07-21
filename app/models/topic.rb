# == Schema Information
#
# Table name: topics
#
#  id         :integer          not null, primary key
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  topic_size :integer
#

class Topic < ApplicationRecord
  MIN_TOPIC_SIZE = 2
  has_many :posts

  scope :ordered_by_date, -> { order("created_at DESC") }
  scope :valid_topics, -> { where("topic_size >= ?", MIN_TOPIC_SIZE).ordered_by_date }
end
