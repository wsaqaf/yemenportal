# == Schema Information
#
# Table name: sources
#
#  id          :integer          not null, primary key
#  link        :string           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  category_id :integer
#
# Indexes
#
#  index_sources_on_category_id  (category_id)
#

class Source < ApplicationRecord
  has_many :posts
  belongs_to :category, optional: true

  validates :link, presence: true
end
