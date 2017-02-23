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
#
# Indexes
#
#  index_posts_on_published_at  (published_at)
#  index_posts_on_source_id     (source_id)
#

class Post < ApplicationRecord
  has_many :post_category
  has_many :categories, through: :post_category
  belongs_to :source

  validates :title, :published_at, :link, presence: true

  scope :ordered_by_publication_date, -> { order("published_at DESC") }
end
