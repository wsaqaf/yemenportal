# == Schema Information
#
# Table name: votes
#
#  id         :integer          not null, primary key
#  user_id    :integer          not null
#  post_id    :integer          not null
#  positive   :boolean
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_votes_on_post_id  (post_id)
#  index_votes_on_user_id  (user_id)
#

class Vote < ApplicationRecord
  belongs_to :post
  belongs_to :user

  scope :votes_posts, ->(posts_ids) { where(post_id: posts_ids) }
  scope :count_by_type, ->(positive) { where(positive: positive).count }

  validates_uniqueness_of :post_id, scope: :user_id
end
