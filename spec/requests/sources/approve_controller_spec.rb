require "rails_helper"

describe Sources::ApproveController, type: :request do
  let(:user) { create(:user, role: "moderator") }

  describe "#update" do
    let(:source) { create :source }
    let(:posts_fetcher_job) { double }
    let(:do_request) { put "/sources/approve/#{source.id}", headers: { "HTTP_REFERER" => "some_path" } }

    it "source approve type" do
      sign_in user
      do_request

      expect(response.status).to eq 302
      expect(response).to redirect_to("some_path")
    end
  end
end
