require "rails_helper"

describe KeywordsService do
  subject { described_class.new(description: "some text one, text. Text, text") }

  let(:post) { build :post, created_at: Time.now, keywords: %w(one two), description: "one two" }
  let(:post_2) { build :post, created_at: (Time.now - 2.hours), keywords: ["opa"], description: "opa" }
  let(:posts) { [post, post_2] }

  describe "#dependent_post" do
    it "find dependent posta" do
      allow(Post).to receive(:where).and_return(posts)
      allow(subject).to receive(:keywords).and_return(%w(one two three))

      expect(subject.dependent_post).to eql([post])
    end
  end

  describe "#keywords" do
    it "find dependent posta" do
      allow(Post).to receive(:last).and_return(posts)

      expect(subject.keywords).to eql(["text"])
    end
  end
end
