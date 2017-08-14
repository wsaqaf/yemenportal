class ReviewComment < ApplicationRecord
  belongs_to :author, class_name: "User"
  belongs_to :topic

  scope :ordered_by_date, -> { order("created_at DESC") }
end
