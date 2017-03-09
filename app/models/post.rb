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
#

class Post < ApplicationRecord
  has_many :post_category
  has_many :categories, through: :post_category

  validates :title, :published_at, :link, presence: true

  scope :ordered_by_publication_date, -> { order("published_at DESC") }
end
