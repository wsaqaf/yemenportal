# == Schema Information
#
# Table name: categories
#
#  id         :integer          not null, primary key
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

class Category < ApplicationRecord
  has_many :post_category
  has_many :posts, through: :post_category

  validates :name, uniqueness: true
  validates :name, presence: true
end
