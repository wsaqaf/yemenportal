# == Schema Information
#
# Table name: posts
#
#  id           :integer          not null, primary key
#  description  :text
#  published_at :datetime
#  link         :string           not null
#  title        :string
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  state        :string           default("pending"), not null
#  image_url    :string
#  topic_id     :integer
#  stemmed_text :text             default("")
#  source_id    :integer          not null
#
# Indexes
#
#  index_posts_on_link          (link)
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#  index_posts_on_topic_id      (topic_id)
#

class Post < ApplicationRecord
  extend Enumerize

  has_many :post_category
  has_many :categories, through: :post_category

  belongs_to :source
  belongs_to :topic, counter_cache: :topic_size, touch: true

  validates :published_at, :link, presence: true
  validates :link, uniqueness: true

  scope :ordered_by_date, -> { order("published_at DESC") }
  scope :source_posts, ->(source_id) { ordered_by_date.where(source_id: source_id) }
  scope :pending_posts, -> { where(state: :pending).ordered_by_date }
  scope :approved_posts, -> { where(state: :approved).ordered_by_date }
  scope :rejected_posts, -> { where(state: :rejected).ordered_by_date }

  scope :posts_by_state, ->(state) { where(state: state).order("published_at DESC") }

  enumerize :state, in: [:approved, :rejected, :pending], default: :pending

  def self.latest
    order("created_at ASC").first
  end

  def self.available_states
    state.values
  end

  def same_posts
    (topic.posts.ordered_by_date - [self]) if topic
  end

  def source_name
    source.name
  end

  def category_names
    if categories.present?
      categories.map(&:name)
    else
      []
    end
  end

  def show_internally?
    source.show_internally?
  end

  def page_content
    PageFetcher.new(self).content
  end
end
