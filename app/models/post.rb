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
#
# Indexes
#
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#

class Post < ApplicationRecord
  extend Enumerize

  has_many :post_category
  has_many :categories, through: :post_category
  has_many :votes
  has_many :users, through: :votes
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
end
