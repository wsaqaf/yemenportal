# == Schema Information
#
# Table name: users
#
#  id         :integer          not null, primary key
#  email      :string
#  first_name :string
#  last_name  :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  role       :enum             default("MEMBER"), not null
#

require 'rails_helper'

describe User do
  %i(email role).each do |field|
    it { is_expected.to validate_presence_of(field) }
  end

  it { is_expected.to validate_uniqueness_of(:email) }
end
