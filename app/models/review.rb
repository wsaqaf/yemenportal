# == Schema Information
#
# Table name: reviews
#
#  id           :integer          not null, primary key
#  topic_id     :integer
#  flag_id      :integer
#  moderator_id :integer
#
# Indexes
#
#  index_reviews_on_flag_id       (flag_id)
#  index_reviews_on_moderator_id  (moderator_id)
#  index_reviews_on_topic_id      (topic_id)
#

class Review < ApplicationRecord
  belongs_to :flag
  belongs_to :topic
  belongs_to :moderator, class_name: "User"

  validates :flag, uniqueness: { scope: [:topic, :moderator] }

  def self.with_resolve_flag(topic, moderator)
    joins(:flag).where(topic: topic, moderator: moderator, flags: { resolve: true })
  end
end
