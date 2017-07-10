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
#  state        :string           default("pending"), not null
#  photo_url    :string
#  topic_id     :integer
#  stemmed_text :text             default("")
#  source_id    :integer          not null
#
# Indexes
#
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#  index_posts_on_topic_id      (topic_id)
#

require "elasticsearch/model"

class Post < ApplicationRecord
  extend Enumerize
  include Elasticsearch::Model
  include Elasticsearch::Model::Callbacks

  has_many :post_category
  has_many :categories, through: :post_category
  has_many :votes
  has_many :users, through: :votes
  has_many :comments
  belongs_to :source
  belongs_to :topic, optional: true

  validates :title, :published_at, :link, presence: true
  validates :link, uniqueness: true

  scope :ordered_by_date, -> { order("published_at DESC") }
  scope :source_posts, ->(source_id) { ordered_by_date.where(source_id: source_id) }
  scope :pending_posts, -> { where(state: :pending).ordered_by_date }
  scope :approved_posts, -> { where(state: :approved).ordered_by_date }
  scope :rejected_posts, -> { where(state: :rejected).ordered_by_date }

  scope :posts_by_state, ->(state) { where(state: state).order("published_at DESC") }

  enumerize :state, in: [:approved, :rejected, :pending], default: :pending

  settings index: { number_of_shards: 1 } do
    mappings dynamic: "false" do
      indexes :title, analyzer: "arabic"
      indexes :description, analyzer: "arabic"
    end
  end

  def self.search(query)
    __elasticsearch__.search(
      {
        query: {
          multi_match: {
            query: query,
            fields: %w(title description)
          }
        }
      }
    ).records
  end

  def self.available_states
    state.values
  end

  def same_posts
    (topic.posts.ordered_by_date - [self]) if topic
  end
end

begin
  Post.__elasticsearch__.client.indices.delete index: Post.index_name
rescue
  nil
end

Post.__elasticsearch__.client.indices.create(
  index: Post.index_name,
  body: { settings: Post.settings.to_hash, mappings: Post.mappings.to_hash }
)
Post.import
