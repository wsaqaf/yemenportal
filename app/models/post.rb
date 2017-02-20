# == Schema Information
#
# Table name: posts
#
#  id          :integer          not null, primary key
#  description :text
#  pub_date    :datetime         not null
#  link        :string           not null
#  title       :string           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

class Post < ApplicationRecord
  has_many :post_category
  has_many :categories, through: :post_category

  validates :title, :pub_date, :link, presence: true
end
