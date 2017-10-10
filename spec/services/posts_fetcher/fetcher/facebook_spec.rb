require "rails_helper"

RSpec.describe PostsFetcher::Fetcher::Facebook do
  describe "constants" do
    it { expect(described_class::TITLE_LENGTH_LIMIT).to eq(100) }
    it { expect(described_class::TITLE_WORDS_SEPARATOR).to eq(/\s/) }
  end

  describe ".fetched_items" do
    let(:source) { instance_double(Source) }
    let(:fetcher) { described_class.new(source) }
    let(:raw_items) { [{ "message" => description, "created_time" => Time.zone.now }] }

    before { allow(fetcher).to receive(:raw_items).and_return(raw_items) }

    context "when post description is not longer than title limit" do
      subject { fetcher.fetched_items.first.title }
      let(:description) { Faker::Lorem.characters(described_class::TITLE_LENGTH_LIMIT - 1) }

      it "uses whole description as a title" do
        expect(subject).to eq(description)
      end
    end

    context "when post description is longer than title limit" do
      subject { fetcher.fetched_items.first.title }
      let(:description) { Faker::Lorem.characters(described_class::TITLE_LENGTH_LIMIT + 1) }

      it "fits title in title limit" do
        expect(subject.length).to eq(described_class::TITLE_LENGTH_LIMIT)
      end

      it "finish title with three dots" do
        expect(subject).to end_with("...")
      end
    end

    context "when title ends in the middle of word" do
      subject { fetcher.fetched_items.first.title }
      let(:start_of_description) { Faker::Lorem.characters(described_class::TITLE_LENGTH_LIMIT - 5) }
      let(:dissected_word) { Faker::Lorem.characters(5) }
      let(:description) { "#{start_of_description} #{dissected_word}" }

      it "cuts title up to the last word" do
        expect(subject).to eq("#{start_of_description}...")
      end
    end
  end
end
