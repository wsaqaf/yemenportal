require "rails_helper"

describe Sources::SuggestController, type: :request do
  let(:user) { create(:user, role: "member") }

  describe "#new" do
    let(:do_request) { get "/sources/suggest/new" }

    it "show a main page" do
      sign_in user
      do_request

      expect(response).to be_success
    end
  end

  describe "#create" do
    let(:params) { { source: { link: "http://asmail.com", name: "some_name", website: "http://asmail.com" } } }
    let(:do_request) { post "/sources/suggest", params: params }

    context "success reques" do
      before do
        allow(SourceProposalMailer).to receive_message_chain(:notification, :deliver_later)
        sign_in(user)
      end

      it "redirect to sources list" do
        do_request

        expect(response.status).to eq 302
        expect(response).to redirect_to(root_path)
      end

      it "sends notification email for every admin" do
        expect(SourceProposalMailer).to receive_message_chain(:notification, :deliver_later)
        do_request
      end
    end

    context "fail request" do
      let(:params) { { source: { link: nil } } }

      it "redirect to create form" do
        sign_in user
        do_request

        expect(response.status).to eq 200
        expect(response).not_to redirect_to(sources_path)
      end
    end
  end
end
