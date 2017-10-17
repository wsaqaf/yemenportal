# == Schema Information
#
# Table name: review_comments
#
#  id         :integer          not null, primary key
#  author_id  :integer
#  body       :text
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  post_id    :integer
#
# Indexes
#
#  index_review_comments_on_author_id  (author_id)
#  index_review_comments_on_post_id    (post_id)
#

class ReviewComment < ApplicationRecord
  belongs_to :author, class_name: "User"
  belongs_to :post

  scope :ordered_by_date, -> { order("created_at ASC") }
end
