# == Schema Information
#
# Table name: sources
#
#  id          :integer          not null, primary key
#  link        :string           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  category_id :integer
#  state       :string           default("valid")
#
# Indexes
#
#  index_sources_on_category_id  (category_id)
#

class Source < ApplicationRecord
  extend Enumerize
  has_many :posts
  has_many :source_logs
  belongs_to :category, optional: true

  validates :link, presence: true
  enumerize :state, in: [:valid, :incorrect_path, :incorrect_stucture, :not_full_info], default: :valid
end
