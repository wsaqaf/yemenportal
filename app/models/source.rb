# == Schema Information
#
# Table name: sources
#
#  id         :integer          not null, primary key
#  link       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

class Source < ApplicationRecord
  has_many :posts

  validates :link, presence: true
end
