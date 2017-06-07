require "rails_helper"

describe PostTag do
  subject { build(:post_tag) }
  it { is_expected.to validate_presence_of(:name) }
end
