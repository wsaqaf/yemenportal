# == Schema Information
#
# Table name: stop_words
#
#  id         :integer          not null, primary key
#  name       :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

class StopWord < ApplicationRecord
  validates :name, presence: true, uniqueness: true
end
