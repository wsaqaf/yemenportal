# == Schema Information
#
# Table name: sources
#
#  id         :integer          not null, primary key
#  link       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

require "rails_helper"

describe Source do
  it { is_expected.to validate_presence_of(:link) }
end
