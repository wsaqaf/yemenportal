# == Schema Information
#
# Table name: post_tags
#
#  id          :integer          not null, primary key
#  user_id     :integer
#  post_id     :integer
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  name        :string
#  description :string
#
# Indexes
#
#  index_post_tags_on_post_id  (post_id)
#  index_post_tags_on_user_id  (user_id)
#

class PostTag < ApplicationRecord
  RESOLVE_TAG = "resolve".freeze
  belongs_to :user
  belongs_to :post

  validates_inclusion_of :name, in: Tag.all.map(&:name) + [RESOLVE_TAG]
  validates :name, presence: true

  scope :resolve, ->(user, post) { where(user: user, post: post, name: RESOLVE_TAG) }
end
