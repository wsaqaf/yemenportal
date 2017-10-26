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

  after_create :add_rating
  after_destroy :subtract_rating

  validates :flag, uniqueness: { scope: [:post, :moderator] }

  def self.with_resolve_flag(post, moderator)
    joins(:flag).where(post: post, moderator: moderator, flags: { resolve: true })
  end

  private

  def add_rating
    post.update(review_rating: post.reload.review_rating + flag.rate)
  end

  def subtract_rating
    post.update(review_rating: post.reload.review_rating - flag.rate)
  end
end
