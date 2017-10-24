require "rails_helper"

RSpec.describe PostsFetcher::FetchedItem do
  describe "constants" do
    it { expect(described_class::TITLE_LENGTH_LIMIT).to eq(100) }
    it { expect(described_class::TITLE_WORDS_SEPARATOR).to eq(/\s/) }
  end

  describe "#title" do
    subject { fetched_item.title }

    let(:fetched_item) { described_class.new(init_params) }

    context "when fetched item was initialized with title" do
      let(:init_params) { { title: passed_title } }
      let(:passed_title) { Faker::Lorem.word }

      it { is_expected.to eq(passed_title) }
    end

    context "when fetched item was not initialized with title" do
      context "when fetched item was initialized with description" do
        let(:init_params) { { description: passed_description } }

        context "when description is nil" do
          let(:passed_description) { nil }

          it { is_expected.to be_nil }
        end

        context "when description is present" do
          let(:passed_description) { Faker::Lorem.word }

          it "extracts title from description" do
            expect(fetched_item)
              .to receive_message_chain(:description, :truncate)
              .with(described_class::TITLE_LENGTH_LIMIT, separator: described_class::TITLE_WORDS_SEPARATOR)
            subject
          end

          context "when sanitized description is blank" do
            let(:passed_description) { "<p>" }

            it { is_expected.to be_blank }
          end
        end
      end

      context "when fetched item was not initialized with description" do
        let(:init_params) { {} }

        it { is_expected.to be_nil }
      end
    end
  end

  describe "#published_at" do
    subject { described_class.new(published_at: publish_time).published_at }

    context "when passing publish time in the future" do
      let(:publish_time) { Time.zone.now + 1.day }

      it "sets current time" do
        is_expected.to be < Time.zone.now
      end
    end

    context "when passing publish time in the past" do
      let(:publish_time) { Time.zone.now - 1.day }

      it "uses this value as publish date" do
        is_expected.to be < Time.zone.now
      end
    end
  end
end
