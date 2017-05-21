require "rails_helper"

describe StopWord do
  it { is_expected.to validate_presence_of(:name) }
end
