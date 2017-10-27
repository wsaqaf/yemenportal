# == Schema Information
#
# Table name: reviews
#
#  id           :integer          not null, primary key
#  flag_id      :integer
#  moderator_id :integer
#  post_id      :integer
#
# Indexes
#
#  index_reviews_on_flag_id       (flag_id)
#  index_reviews_on_moderator_id  (moderator_id)
#  index_reviews_on_post_id       (post_id)
#

class Review < ApplicationRecord
  belongs_to :flag
  belongs_to :post
  belongs_to :moderator, class_name: "User"

  validates :flag, uniqueness: { scope: [:post, :moderator] }

  def self.with_resolve_flag(post, moderator)
    joins(:flag).where(post: post, moderator: moderator, flags: { resolve: true })
  end

  def self.reviews_rate
    joins(:flag).sum("flags.rate")
  end
end
