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
#  source_id    :integer
#  state        :string           default("pending"), not null
#  photo_url    :string
#  keywords     :string           default("{}"), is an Array
#
# Indexes
#
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#

class Post < ApplicationRecord
  SAME_POST_COUNT = 3
  extend Enumerize

  has_many :post_associations, foreign_key: :main_post_id
  has_many :posts, through: :post_associations, source: :dependent_post

  has_many :post_category
  has_many :categories, through: :post_category
  has_many :votes
  has_many :users, through: :votes
  has_many :comments
  belongs_to :source

  validates :title, :published_at, :link, presence: true

  scope :ordered_by_date, -> { order("published_at DESC") }
  scope :source_posts, ->(source_id) { ordered_by_date.where(source_id: source_id) }
  scope :pending_posts, -> { where(state: :pending).ordered_by_date }
  scope :approved_posts, -> { where(state: :approved).ordered_by_date }
  scope :rejected_posts, -> { where(state: :rejected).ordered_by_date }

  scope :posts_by_state, ->(state) { where(state: state).order("published_at DESC") }

  enumerize :state, in: [:approved, :rejected, :pending], default: :pending

  def self.available_states
    state.values
  end

  def same_posts
    first_path = posts.approved_posts
    second_path = Post.joins(:post_associations).where("post_associations.dependent_post_id = #{id}").approved_posts
    (first_path + second_path).sample(SAME_POST_COUNT)
  end
end
