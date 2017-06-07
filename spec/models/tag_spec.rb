require "rails_helper"

describe Tag do
  subject { build(:tag) }
  it { is_expected.to validate_uniqueness_of(:name) }
  it { is_expected.to validate_presence_of(:name) }
end
