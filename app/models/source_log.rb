# == Schema Information
#
# Table name: logs
#
#  id          :integer          not null, primary key
#  state       :string
#  source_id   :integer          not null
#  posts_count :integer          default("0")
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_logs_on_source_id  (source_id)
#

class SourceLog < ApplicationRecord
  extend Enumerize
  belongs_to :source

  validates :posts_count, numericality: { greater_than_or_equal_to: 0 }
  enumerize :state, in: [:valid, :invalid], default: :valid

  scope :ordered, -> { order("created_at DESC").limit(24) }
end
