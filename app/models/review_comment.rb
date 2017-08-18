# == Schema Information
#
# Table name: review_comments
#
#  id         :integer          not null, primary key
#  author_id  :integer
#  topic_id   :integer
#  body       :text
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_review_comments_on_author_id  (author_id)
#  index_review_comments_on_topic_id   (topic_id)
#

class ReviewComment < ApplicationRecord
  belongs_to :author, class_name: "User"
  belongs_to :topic

  scope :ordered_by_date, -> { order("created_at ASC") }
end
