require "rails_helper"

describe Source do
  it { is_expected.to validate_presence_of(:link) }
  it { is_expected.to enumerize(:state).in(:valid, :incorrect_path, :incorrect_stucture, :not_full_info, :other) }

  describe ".ordered_by_date" do
    subject { described_class.ordered_by_date }

    let!(:old_source) { create(:source) }
    let!(:new_source) { create(:source) }

    it "returns new sources first" do
      is_expected.to eq([new_source, old_source])
    end
  end

  describe "#facebook_page" do
    let(:fb_source) { build(:source, link: "https://www.facebook.com/ByRoR", source_type: :facebook) }
    let(:rss_source) { build(:source, link: "https://some_name/ByRoR", source_type: :rss) }

    it { expect(fb_source.facebook_page).to eql("ByRoR") }
    it { expect(rss_source.facebook_page).to be(nil) }
  end
end
